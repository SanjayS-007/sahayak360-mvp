"use client";

import { useEffect, useState } from "react";
import { toast } from "sonner";
import { AppShell } from "@/components/shared/app-shell";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { practiceApi } from "@/lib/api";
import {
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  Lightbulb,
} from "lucide-react";

// Embedded flashcard data from kc_context
const FLASHCARD_DATA: Record<string, { title: string; cards: Array<{ front: string; back: string }> }> = {
  "ALG-LINEAR-EQ": {
    title: "Linear Equations",
    cards: [
      { front: "What is the slope-intercept form?", back: "y = mx + b, where m = slope, b = y-intercept" },
      { front: "How to find slope between two points?", back: "m = (y₂ - y₁) / (x₂ - x₁)" },
      { front: "When are two lines parallel?", back: "When they have the same slope (m₁ = m₂) but different y-intercepts" },
      { front: "What does the y-intercept represent?", back: "The point where the line crosses the y-axis (x = 0)" },
      { front: "How to solve: 3x + 5 = 20?", back: "Subtract 5: 3x = 15, then divide by 3: x = 5" },
    ],
  },
  "ALG-QUAD-EQ": {
    title: "Quadratic Equations",
    cards: [
      { front: "What is the quadratic formula?", back: "x = (-b ± √(b²-4ac)) / 2a" },
      { front: "What does the discriminant tell us?", back: "D = b²-4ac. D>0: 2 real roots, D=0: 1 root, D<0: no real roots" },
      { front: "Sum of roots of ax²+bx+c=0?", back: "-b/a (Vieta's formula)" },
      { front: "Product of roots of ax²+bx+c=0?", back: "c/a (Vieta's formula)" },
      { front: "How to find the vertex?", back: "x = -b/2a, then substitute to find y" },
    ],
  },
  "GEO-TRIANGLES": {
    title: "Triangles",
    cards: [
      { front: "Pythagoras Theorem?", back: "In a right triangle: a² + b² = c² (c is hypotenuse)" },
      { front: "Sum of angles in a triangle?", back: "Always 180°" },
      { front: "Area of a triangle?", back: "½ × base × height" },
      { front: "What makes triangles similar?", back: "AA (two angles equal), SSS (sides proportional), SAS (included angle + proportional sides)" },
      { front: "Centroid divides median in ratio?", back: "2:1 from vertex to midpoint of opposite side" },
    ],
  },
  "GEO-CIRCLES": {
    title: "Circles",
    cards: [
      { front: "Area of a circle?", back: "πr²" },
      { front: "Circumference of a circle?", back: "2πr or πd" },
      { front: "Tangent property?", back: "Tangent is perpendicular to radius at point of contact" },
      { front: "Angle in a semicircle?", back: "Always 90° (Thales' theorem)" },
      { front: "Sector area formula?", back: "(θ/360°) × πr²" },
    ],
  },
  "STAT-MEASURES": {
    title: "Statistical Measures",
    cards: [
      { front: "Mean formula?", back: "Sum of all values / Number of values" },
      { front: "Median for even count?", back: "Average of the two middle values when sorted" },
      { front: "Which measure resists outliers?", back: "Median (not affected by extreme values)" },
      { front: "Standard deviation measures?", back: "How spread out values are from the mean" },
      { front: "If all values multiplied by k, what happens to SD?", back: "SD also gets multiplied by k" },
    ],
  },
  "STAT-PROBABILITY": {
    title: "Probability",
    cards: [
      { front: "P(A or B) formula?", back: "P(A) + P(B) - P(A and B)" },
      { front: "Independent events?", back: "P(A and B) = P(A) × P(B)" },
      { front: "Complementary rule?", back: "P(not A) = 1 - P(A)" },
      { front: "Expected value of fair die?", back: "(1+2+3+4+5+6)/6 = 3.5" },
      { front: "Bayes' Theorem?", back: "P(A|B) = P(B|A)×P(A) / P(B)" },
    ],
  },
  "TRIG-BASIC": {
    title: "Trigonometry",
    cards: [
      { front: "SOH-CAH-TOA?", back: "Sin=Opp/Hyp, Cos=Adj/Hyp, Tan=Opp/Adj" },
      { front: "Pythagorean identity?", back: "sin²θ + cos²θ = 1" },
      { front: "sin 30°, cos 60°?", back: "Both equal 1/2" },
      { front: "tan 45°?", back: "1 (because sin45° = cos45°)" },
      { front: "cos(90° - θ) = ?", back: "sin θ (complementary angle identity)" },
    ],
  },
};

export default function FlashcardsPage() {
  const [selectedKC, setSelectedKC] = useState<string | null>(null);
  const [currentCard, setCurrentCard] = useState(0);
  const [flipped, setFlipped] = useState(false);
  const [availableKCs, setAvailableKCs] = useState<string[]>([]);

  useEffect(() => {
    setAvailableKCs(Object.keys(FLASHCARD_DATA));
  }, []);

  const deck = selectedKC ? FLASHCARD_DATA[selectedKC] : null;
  const card = deck?.cards[currentCard];

  function nextCard() {
    if (deck && currentCard < deck.cards.length - 1) {
      setCurrentCard(currentCard + 1);
      setFlipped(false);
    }
  }

  function prevCard() {
    if (currentCard > 0) {
      setCurrentCard(currentCard - 1);
      setFlipped(false);
    }
  }

  function resetDeck() {
    setCurrentCard(0);
    setFlipped(false);
  }

  return (
    <AppShell requiredRole="student">
      <div className="space-y-6 max-w-2xl mx-auto">
        <div className="flex items-center gap-3">
          <BookOpen className="h-7 w-7 text-purple-600" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Flashcards</h2>
            <p className="text-sm text-gray-500">Quick revision of key concepts</p>
          </div>
        </div>

        {!selectedKC ? (
          /* Topic Selection */
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Choose a Topic</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 sm:grid-cols-2">
                {availableKCs.map((kc) => (
                  <button
                    key={kc}
                    onClick={() => { setSelectedKC(kc); setCurrentCard(0); setFlipped(false); }}
                    className="rounded-lg border p-4 text-left hover:border-purple-400 hover:bg-purple-50 transition-colors"
                  >
                    <p className="font-medium text-gray-900">{FLASHCARD_DATA[kc].title}</p>
                    <p className="text-xs text-gray-500 mt-1">{FLASHCARD_DATA[kc].cards.length} cards</p>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>
        ) : (
          /* Flashcard View */
          <>
            <div className="flex items-center justify-between">
              <Button variant="outline" size="sm" onClick={() => { setSelectedKC(null); resetDeck(); }}>
                ← All Topics
              </Button>
              <Badge variant="outline">{deck?.title} • {currentCard + 1}/{deck?.cards.length}</Badge>
            </div>

            {/* Card */}
            <div
              onClick={() => setFlipped(!flipped)}
              className="cursor-pointer perspective-1000"
            >
              <div className={`relative w-full min-h-[240px] rounded-xl border-2 transition-all duration-500 ${
                flipped ? "border-purple-300 bg-purple-50" : "border-indigo-200 bg-white"
              } flex items-center justify-center p-8 shadow-sm hover:shadow-md`}>
                {!flipped ? (
                  <div className="text-center">
                    <Lightbulb className="mx-auto h-8 w-8 text-indigo-300 mb-4" />
                    <p className="text-lg font-medium text-gray-800">{card?.front}</p>
                    <p className="text-xs text-gray-400 mt-4">Tap to reveal answer</p>
                  </div>
                ) : (
                  <div className="text-center">
                    <p className="text-lg text-purple-800 font-medium">{card?.back}</p>
                    <p className="text-xs text-gray-400 mt-4">Tap to see question</p>
                  </div>
                )}
              </div>
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-center gap-4">
              <Button variant="outline" size="sm" onClick={prevCard} disabled={currentCard === 0}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button variant="outline" size="sm" onClick={resetDeck}>
                <RotateCcw className="h-4 w-4 mr-1" /> Reset
              </Button>
              <Button variant="outline" size="sm" onClick={nextCard} disabled={currentCard === (deck?.cards.length || 1) - 1}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </>
        )}
      </div>
    </AppShell>
  );
}
