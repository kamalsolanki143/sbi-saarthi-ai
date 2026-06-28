"use client";

import React from "react";
import { motion } from "framer-motion";
import { ArrowRight, Mic, ShieldCheck, Trash2 } from "lucide-react";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost" | "danger";
  state?: "default" | "hover" | "active" | "disabled";
  iconLeft?: React.ReactNode;
  iconRight?: React.ReactNode;
  fullWidth?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      children,
      variant = "primary",
      state = "default",
      iconLeft,
      iconRight,
      fullWidth = false,
      disabled,
      className = "",
      ...props
    },
    ref
  ) => {
    const isDisabled = state === "disabled" || disabled;

    const baseStyles =
      "relative flex items-center justify-center gap-2 h-[48px] px-6 py-[14px] rounded-full font-sans text-[16px] font-medium tracking-[0.02em] transition-all duration-200 select-none outline-none focus:ring-2 focus:ring-[#00D4FF]";

    const variantStyles = {
      primary:
        "bg-[#0F52BA] text-[#FFFFFF] hover:bg-[#1662D8] hover:shadow-[0_4px_16px_0_rgba(7,27,59,0.5)] active:bg-[#0D429A]",
      secondary:
        "bg-[#13264A]/80 border border-[#284C8F] text-[#FFFFFF] hover:bg-[#13264A] hover:border-[#00D4FF]/50 active:bg-[#0E1E3B]",
      ghost: "bg-transparent text-[#00D4FF] hover:bg-[#00D4FF]/10 active:bg-[#00D4FF]/20",
      danger:
        "bg-[#FF5252]/20 border border-[#FF5252] text-[#FF5252] hover:bg-[#FF5252]/30 active:bg-[#FF5252]/40",
    };

    const disabledStyles =
      "bg-[#FFFFFF]/10 border-none text-[#FFFFFF]/30 cursor-not-allowed shadow-none hover:shadow-none hover:bg-[#FFFFFF]/10 active:bg-[#FFFFFF]/10";

    const currentStyles = isDisabled
      ? disabledStyles
      : variantStyles[variant] || variantStyles.primary;

    return (
    <motion.button
        ref={ref}
        disabled={isDisabled}
        whileTap={!isDisabled ? { scale: 0.98 } : undefined}
        className={`${baseStyles} ${currentStyles} ${
          fullWidth ? "w-full" : ""
        } ${className}`}
        {...props}
      >
        {iconLeft && <span className="flex-shrink-0">{iconLeft}</span>}
        <span className="truncate">{children}</span>
        {iconRight && <span className="flex-shrink-0">{iconRight}</span>}
      </motion.button>
    );
  }
);

Button.displayName = "Button";

export const ButtonsShowcase: React.FC = () => {
  return (
    <div className="space-y-8 text-[#FFFFFF]">
      <div>
        <h2 className="text-2xl font-bold tracking-tight mb-2">
          Button Components
        </h2>
        <p className="text-sm text-[#FFFFFF]/60">
          48px Touch-Target Enterprise Action Stack
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 bg-[#0E1E3B]/40 p-6 rounded-2xl border border-[#284C8F]/30">
        <div className="space-y-4">
          <span className="text-xs font-mono text-[#00D4FF]">Primary</span>
          <div className="space-y-3">
            <Button variant="primary">Default</Button>
            <Button variant="primary" iconLeft={<Mic className="w-5 h-5" />}>
              Voice Pay
            </Button>
            <Button variant="primary" state="disabled">
              Disabled
            </Button>
          </div>
        </div>

        <div className="space-y-4">
          <span className="text-xs font-mono text-[#00D4FF]">Secondary</span>
          <div className="space-y-3">
            <Button variant="secondary">Default</Button>
            <Button
              variant="secondary"
              iconRight={<ArrowRight className="w-5 h-5" />}
            >
              Action
            </Button>
            <Button variant="secondary" state="disabled">
              Disabled
            </Button>
          </div>
        </div>

        <div className="space-y-4">
          <span className="text-xs font-mono text-[#00D4FF]">Ghost</span>
          <div className="space-y-3">
            <Button variant="ghost">Default</Button>
            <Button
              variant="ghost"
              iconLeft={<ShieldCheck className="w-5 h-5" />}
            >
              Secure ID
            </Button>
            <Button variant="ghost" state="disabled">
              Disabled
            </Button>
          </div>
        </div>

        <div className="space-y-4">
          <span className="text-xs font-mono text-[#FF5252]">Danger</span>
          <div className="space-y-3">
            <Button variant="danger">Default</Button>
            <Button variant="danger" iconLeft={<Trash2 className="w-5 h-5" />}>
              Revoke
            </Button>
            <Button variant="danger" state="disabled">
              Disabled
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};