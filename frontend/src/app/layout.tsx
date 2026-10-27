import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Chat with Code — AI Repository Analysis',
  description:
    'Ask questions, explore architecture, and analyze any public GitHub repository using AI-powered RAG with Google Gemini and BAAI embeddings.',
  keywords: ['rag', 'code analysis', 'gemini', 'github', 'llamaindex', 'ai', 'developer tools'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="min-h-screen bg-surface-50 text-surface-900 dark:bg-surface-950 dark:text-surface-100 antialiased selection:bg-brand-500/20 selection:text-brand-600 dark:selection:text-brand-300">
        {children}
      </body>
    </html>
  );
}
