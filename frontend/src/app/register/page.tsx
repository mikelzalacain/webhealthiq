"use client";

import { Suspense } from "react";
import AuthForm from "@/components/AuthForm";

export default function RegisterPage() {
  return (
    <Suspense fallback={<div className="min-h-[50vh]" />}>
      <AuthForm mode="register" />
    </Suspense>
  );
}
