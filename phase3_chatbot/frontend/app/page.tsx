import Link from "next/link";
import { Button } from "@/components/ui/Button";
import { CheckCircle2, Sparkles, Zap, Shield } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-blue-50 to-pink-50 dark:from-gray-900 dark:via-purple-900 dark:to-blue-900">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/20">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-6 w-6 text-primary" />
            <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
              TaskFlow
            </span>
          </div>
          <div className="flex items-center gap-4">
            <Link href="/signin">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/signup">
              <Button variant="gradient">Get Started</Button>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="container mx-auto px-4 pt-32 pb-20">
        <div className="max-w-4xl mx-auto text-center space-y-8 animate-fade-in">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-4">
            <Sparkles className="h-4 w-4" />
            <span>The Future of Task Management</span>
          </div>

          <h1 className="text-6xl md:text-7xl font-bold tracking-tight">
            <span className="bg-gradient-to-r from-purple-600 via-blue-600 to-pink-600 bg-clip-text text-transparent">
              Organize Your Life
            </span>
            <br />
            <span className="text-foreground">With Intelligence</span>
          </h1>

          <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Experience the next generation of task management. Beautiful, powerful, and designed for the way you work.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link href="/signup">
              <Button size="lg" variant="gradient" className="text-lg px-8 h-14 min-w-[200px]">
                Start Free Today
              </Button>
            </Link>
            <Link href="/signin">
              <Button size="lg" variant="outline" className="text-lg px-8 h-14 min-w-[200px]">
                Sign In
              </Button>
            </Link>
          </div>

          <p className="text-sm text-muted-foreground">
            No credit card required • Free forever plan available
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto mt-32">
          <div className="glass rounded-2xl p-8 space-y-4 hover:scale-105 transition-transform duration-300">
            <div className="h-12 w-12 rounded-xl gradient-purple flex items-center justify-center">
              <Zap className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold">Lightning Fast</h3>
            <p className="text-muted-foreground">
              Create, organize, and complete tasks in milliseconds. Built for speed and efficiency.
            </p>
          </div>

          <div className="glass rounded-2xl p-8 space-y-4 hover:scale-105 transition-transform duration-300">
            <div className="h-12 w-12 rounded-xl gradient-blue flex items-center justify-center">
              <Sparkles className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold">Smart Organization</h3>
            <p className="text-muted-foreground">
              Priorities, tags, recurring tasks, and intelligent reminders to keep you on track.
            </p>
          </div>

          <div className="glass rounded-2xl p-8 space-y-4 hover:scale-105 transition-transform duration-300">
            <div className="h-12 w-12 rounded-xl gradient-green flex items-center justify-center">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <h3 className="text-xl font-semibold">Secure & Private</h3>
            <p className="text-muted-foreground">
              Your data is encrypted and protected. Complete privacy with industry-leading security.
            </p>
          </div>
        </div>

        {/* CTA Section */}
        <div className="max-w-3xl mx-auto text-center mt-32 glass rounded-3xl p-12 space-y-6">
          <h2 className="text-4xl font-bold">Ready to Transform Your Productivity?</h2>
          <p className="text-lg text-muted-foreground">
            Join thousands of professionals who have revolutionized their workflow with TaskFlow.
          </p>
          <Link href="/signup">
            <Button size="lg" variant="gradient" className="text-lg px-12 h-14">
              Get Started Now
            </Button>
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/20 mt-32 py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>© 2026 TaskFlow. Built with ❤️ for productivity enthusiasts.</p>
        </div>
      </footer>
    </div>
  );
}
