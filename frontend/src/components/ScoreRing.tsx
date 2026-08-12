"use client";

import { useEffect, useRef, useState } from "react";
import { useI18n } from "@/lib/i18n/LanguageProvider";

interface ScoreRingProps {
  score: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
  animate?: boolean;
  className?: string;
}

export default function ScoreRing({
  score,
  size = 140,
  strokeWidth = 8,
  label,
  animate = true,
  className = "",
}: ScoreRingProps) {
  const { t } = useI18n();
  const [displayScore, setDisplayScore] = useState(animate ? 0 : score);
  const [isVisible, setIsVisible] = useState(!animate);
  const ref = useRef<HTMLDivElement>(null);

  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (displayScore / 100) * circumference;

  const getColor = (s: number) => {
    if (s >= 90) return "#1f8a5b";
    if (s >= 70) return "#0d6e63";
    if (s >= 50) return "#c47c14";
    if (s >= 30) return "#e4572e";
    return "#c53d3d";
  };

  const getLabel = (s: number) => {
    if (s >= 90) return t("score.excellent");
    if (s >= 70) return t("score.good");
    if (s >= 50) return t("score.ok");
    if (s >= 30) return t("score.fair");
    return t("score.critical");
  };

  const stroke = getColor(score);

  useEffect(() => {
    if (!animate) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.3 }
    );
    if (ref.current) observer.observe(ref.current);
    return () => observer.disconnect();
  }, [animate]);

  useEffect(() => {
    if (!isVisible || !animate) return;
    const duration = 1200;
    const startTime = performance.now();
    const tick = (now: number) => {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      setDisplayScore(Math.round(eased * score));
      if (progress < 1) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  }, [isVisible, score, animate]);

  return (
    <div ref={ref} className={`flex flex-col items-center gap-2 ${className}`}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="transform -rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#d5e0dc"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={stroke}
            strokeWidth={strokeWidth}
            strokeLinecap="butt"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            style={{
              transition: animate ? "stroke-dashoffset 1.2s cubic-bezier(0.4, 0, 0.2, 1)" : "none",
            }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span
            className="font-display font-bold leading-none text-ink"
            style={{ fontSize: size * 0.28 }}
          >
            {displayScore}
          </span>
          <span className="text-muted font-medium" style={{ fontSize: size * 0.09 }}>
            / 100
          </span>
        </div>
      </div>
      {label && (
        <span className="text-xs font-semibold text-muted uppercase tracking-[0.16em]">
          {label}
        </span>
      )}
      <span
        className="text-xs font-semibold px-2.5 py-1 rounded-md"
        style={{ background: `${stroke}18`, color: stroke }}
      >
        {getLabel(score)}
      </span>
    </div>
  );
}
