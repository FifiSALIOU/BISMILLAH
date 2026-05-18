import { Button } from '@/components/ui/button';
import { useState, useEffect } from 'react';

const Hero = () => {
  const [currentImage, setCurrentImage] = useState(0);
  const images = [
    "/lovable-uploads/Hijab.png",
    "/lovable-uploads/Dame.png"
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentImage((prev) => (prev + 1) % images.length);
    }, 4000); // Change image every 4 seconds

    return () => clearInterval(interval);
  }, [images.length]);

  return (
    <section className="relative bg-background overflow-hidden h-[70vh]">
      <div className="relative w-full h-full">
        {images.map((image, index) => (
          <div
            key={index}
            className={`absolute inset-0 transition-opacity duration-1000 ${
              index === currentImage ? 'opacity-100' : 'opacity-0'
            }`}
          >
            <img 
              src={image}
              alt="Notre équipe professionnelle"
              className="w-full h-full object-cover"
            />
          </div>
        ))}
        

      </div>
    </section>
  );
};

export default Hero;