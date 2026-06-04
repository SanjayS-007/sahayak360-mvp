"use client";

import { useState } from "react";
import { Info, X } from "lucide-react";

interface InfoTooltipProps {
  title: string;
  sections: {
    heading: string;
    content: string;
  }[];
}

export function InfoTooltip({ title, sections }: InfoTooltipProps) {
  const [open, setOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="inline-flex items-center justify-center h-6 w-6 rounded-full text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
        title="Learn more"
      >
        <Info className="h-4 w-4" />
      </button>

      {open && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 bg-black/30 z-50 animate-in fade-in"
            onClick={() => setOpen(false)}
          />
          {/* Panel */}
          <div className="fixed right-0 top-0 h-full w-full max-w-md bg-white shadow-2xl z-50 overflow-y-auto animate-in slide-in-from-right duration-200">
            <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">{title}</h2>
              <button
                onClick={() => setOpen(false)}
                className="h-8 w-8 rounded-full flex items-center justify-center hover:bg-gray-100"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            <div className="px-6 py-5 space-y-6">
              {sections.map((section, i) => (
                <div key={i}>
                  <h3 className="text-sm font-semibold text-indigo-600 uppercase tracking-wide mb-2">
                    {section.heading}
                  </h3>
                  <p className="text-sm text-gray-700 leading-relaxed">
                    {section.content}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </>
  );
}
