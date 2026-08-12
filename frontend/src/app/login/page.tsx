"use client";

import { Suspense } from "react";
import AuthForm from "@/components/AuthForm";

export default function LoginPage() {
  return (
    <Suspense fallback={<div className="min-h-[50vh]" />}>
      <AuthForm mode="login" />
    </Suspense>
  );
}
