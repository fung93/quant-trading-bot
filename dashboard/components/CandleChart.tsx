"use client";

import { useEffect, useRef } from "react";
import {
  CandlestickSeries,
  ColorType,
  createChart,
  createSeriesMarkers,
  HistogramSeries,
  type IChartApi,
  type ISeriesApi,
  type ISeriesMarkersPluginApi,
  type SeriesMarker,
  type Time,
  type UTCTimestamp,
} from "lightweight-charts";
import type { Candle, Timeframe } from "@/lib/data";

export interface CandleChartProps {
  symbol: string;
  timeframe: Timeframe;
  candles: Candle[];
  /** Trade markers (Phase 2): times are raw UNIX seconds UTC; the component
   *  applies the same timezone shift as the candles. */
  markers?: SeriesMarker<Time>[];
}

const UP = "#26a69a";
const DOWN = "#ef5350";

export default function CandleChart({ symbol, timeframe, candles, markers }: CandleChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const markersRef = useRef<ISeriesMarkersPluginApi<Time> | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: "transparent" },
        textColor: "#9ca3af",
        attributionLogo: true,
      },
      grid: {
        vertLines: { color: "rgba(255, 255, 255, 0.06)" },
        horzLines: { color: "rgba(255, 255, 255, 0.06)" },
      },
      rightPriceScale: { borderColor: "rgba(255, 255, 255, 0.15)" },
      timeScale: { borderColor: "rgba(255, 255, 255, 0.15)" },
    });

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: UP,
      downColor: DOWN,
      borderUpColor: UP,
      borderDownColor: DOWN,
      wickUpColor: UP,
      wickDownColor: DOWN,
    });
    chart.priceScale("right").applyOptions({
      scaleMargins: { top: 0.05, bottom: 0.25 },
    });

    // Volume as an overlay histogram on its own hidden scale, squeezed into
    // the bottom fifth of the pane.
    const volumeSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
      lastValueVisible: false,
      priceLineVisible: false,
    });
    chart.priceScale("volume").applyOptions({
      scaleMargins: { top: 0.82, bottom: 0 },
      visible: false,
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    volumeSeriesRef.current = volumeSeries;

    return () => {
      chart.remove();
      chartRef.current = null;
      candleSeriesRef.current = null;
      volumeSeriesRef.current = null;
    };
  }, []);

  useEffect(() => {
    const chart = chartRef.current;
    const candleSeries = candleSeriesRef.current;
    const volumeSeries = volumeSeriesRef.current;
    if (!chart || !candleSeries || !volumeSeries) return;

    // lightweight-charts renders timestamps as UTC; shifting by the browser
    // offset makes axis/crosshair labels show local wall time (owner UTC+8).
    const tzShift = -new Date().getTimezoneOffset() * 60;

    candleSeries.setData(
      candles.map((c) => ({
        time: (c.time + tzShift) as UTCTimestamp,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      }))
    );
    volumeSeries.setData(
      candles.map((c) => ({
        time: (c.time + tzShift) as UTCTimestamp,
        value: c.volume,
        color: c.close >= c.open ? "rgba(38, 166, 154, 0.4)" : "rgba(239, 83, 80, 0.4)",
      }))
    );

    if (markers?.length) {
      const shifted = markers.map((m) => ({
        ...m,
        time: ((m.time as number) + tzShift) as UTCTimestamp,
      }));
      if (markersRef.current) {
        markersRef.current.setMarkers(shifted);
      } else {
        markersRef.current = createSeriesMarkers(candleSeries, shifted);
      }
    }

    chart.applyOptions({
      timeScale: { timeVisible: timeframe === "1h", secondsVisible: false },
    });
    chart.timeScale().fitContent();
  }, [candles, timeframe, markers]);

  return (
    <section className="rounded-lg border border-white/10 bg-white/[0.02] p-3">
      <h2 className="mb-2 font-mono text-sm text-gray-300">
        {symbol} <span className="text-gray-500">· {timeframe}</span>
      </h2>
      <div ref={containerRef} className="h-[320px] w-full md:h-[400px]" />
    </section>
  );
}
