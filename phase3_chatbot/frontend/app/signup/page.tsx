"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { CheckCircle2, ArrowRight, User, Mail, Lock, AlertCircle } from "lucide-react";
import { authApi } from "@/lib/api";

export default function SignupPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    
    // Validate password length (72 bytes max)
    const passwordByteLength = new Blob([formData.password]).size;
    if (passwordByteLength > 72) {
      setError("Password is too long. Please use a password with maximum 72 characters.");
      return;
    }
    
    setLoading(true);

    try {
      // Call signup API
      const result = await authApi.signup(formData);

      // Save user_id from response to localStorage
      if (result.user && result.user.id) {
        localStorage.setItem("user_id", result.user.id.toString());
      }

      // Redirect to dashboard
      router.push("/dashboard");
    } catch (err: any) {
      setError(err.message || "Failed to create account");
    } finally {
      setLoading(false);
    }
  };

  // Handle password change with validation
  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    const byteLength = new Blob([value]).size;
    
    if (byteLength > 72) {
      setError("Password is too long (maximum 72 characters)");
      return;
    }
    
    setError("");
    setFormData({ ...formData, password: value });
  };

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-background">
        <div className="w-full max-w-md space-y-8 animate-fade-in">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-8 w-8 text-primary" />
            <span className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              TaskFlow
            </span>
          </div>

          {/* Header */}
          <div className="space-y-2">
            <h1 className="text-4xl font-bold tracking-tight">Create Account</h1>
            <p className="text-muted-foreground">
              Start organizing your tasks today
            </p>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-destructive/10 border border-destructive/30 rounded-lg p-4 flex items-start gap-3 animate-scale-in">
              <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
              <div className="flex-1">
                <p className="text-sm text-destructive font-medium">{error}</p>
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="name" className="text-sm font-medium">
                  Full Name
                </label>
                <div className="relative">
                  <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                  <Input
                    id="name"
                    type="text"
                    placeholder="John Doe"
                    className="pl-10"
                    value={formData.name}
                    onChange={(e) =>
                      setFormData({ ...formData, name: e.target.value })
                    }
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium">
                  Email Address
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="you@example.com"
                    className="pl-10"
                    value={formData.email}
                    onChange={(e) =>
                      setFormData({ ...formData, email: e.target.value })
                    }
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <label htmlFor="password" className="text-sm font-medium">
                  Password
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-muted-foreground" />
                  <Input
                    id="password"
                    type="password"
                    placeholder="At least 8 characters"
                    className="pl-10"
                    maxLength={72}
                    value={formData.password}
                    onChange={handlePasswordChange}
                    required
                    minLength={8}
                  />
                </div>
                <p className="text-xs text-muted-foreground">
                  Must be at least 8 characters (maximum 72 characters)
                </p>
              </div>
            </div>

            <Button
              type="submit"
              className="w-full"
              variant="gradient"
              size="lg"
              disabled={loading}
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="h-4 w-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Creating Account...
                </span>
              ) : (
                <span className="flex items-center gap-2">
                  Create Account
                  <ArrowRight className="h-4 w-4" />
                </span>
              )}
            </Button>

            <div className="text-center text-sm text-muted-foreground">
              Already have an account?{" "}
              <Link
                href="/signin"
                className="text-primary hover:underline font-medium"
              >
                Sign in
              </Link>
            </div>
          </form>

          {/* Terms */}
          <p className="text-xs text-muted-foreground text-center">
            By creating an account, you agree to our{" "}
            <Link href="#" className="underline hover:text-foreground">
              Terms of Service
            </Link>{" "}
            and{" "}
            <Link href="#" className="underline hover:text-foreground">
              Privacy Policy
            </Link>
          </p>
        </div>
      </div>

      {/* Right Side - Image/Branding */}
      <div className="hidden lg:flex flex-1 bg-gradient-to-br from-purple-600 via-blue-600 to-pink-600 items-center justify-center p-8">
        <div className="max-w-md space-y-6 text-white">
          <h2 className="text-4xl font-bold">
            Welcome to the Future of Productivity
          </h2>
          <p className="text-lg text-white/90">
            Join thousands of professionals who have transformed their workflow
            with TaskFlow's intelligent task management system.
          </p>
          <div className="space-y-4 pt-8">
            <div className="flex items-start gap-3">
              <CheckCircle2 className="h-6 w-6 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold">Smart Organization</h3>
                <p className="text-white/80 text-sm">
                  Priorities, tags, and recurring tasks
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle2 className="h-6 w-6 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold">Intelligent Reminders</h3>
                <p className="text-white/80 text-sm">
                  Never miss a deadline again
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CheckCircle2 className="h-6 w-6 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold">Powerful Search</h3>
                <p className="text-white/80 text-sm">
                  Find anything in milliseconds
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
