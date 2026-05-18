import Header from '@/components/Header';
import Hero from '@/components/Hero';
import TeamSection from '@/components/TeamSection';
import FloatingChatbot from '@/components/FloatingChatbot';

const Index = () => {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <Hero />
      <TeamSection />
      <FloatingChatbot />
    </div>
  );
};

export default Index;