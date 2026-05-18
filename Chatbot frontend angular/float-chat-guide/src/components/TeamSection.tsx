const TeamSection = () => {
  const teamMembers = [
    {
      id: 1,
      name: "ESPACE SALARIÉ",
      image: "/lovable-uploads/b34eb5ee-0792-450d-937f-298acf7c512b.png"
    },
    {
      id: 2,
      name: "ESPACE EMPLOYEUR", 
      image: "/lovable-uploads/67a62b4c-ac7a-409f-8144-2a6c05dd0f06.png"
    },
    /*{
      id: 3,
      name: "Prestations Familiales",
      image: "/lovable-uploads/8eb440c0-eeb7-4c77-abcc-270e7591e688.png"
    },*/
    {
      id: 4,
      name: "ESPACE ALLOCATAIRE",
      image: "/lovable-uploads/3011e609-985c-428f-8ce8-8d74ba358169.png"
    }
  ];

  return (
    <section className="py-16 bg-background">
      <div className="container mx-auto px-6">
        <div className="grid lg:grid-cols-3 gap-8 items-start">
          {/* Left - Team Section */}
          <div className="text-center lg:col-span-2">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-8">
              Une Équipe à Votre Écoute
            </h2>
            
            {/* Team Grid - 4 circular photos */}
            <div className="flex flex-wrap justify-center gap-6">
              {teamMembers.map((member) => (
                <div key={member.id} className="text-center">
                  <div className="w-40 h-40 md:w-48 md:h-48 rounded-full overflow-hidden mx-auto mb-3 shadow-lg">
                    <img 
                      src={member.image}
                      alt={member.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <p className="text-sm font-medium text-foreground">
                    {member.name}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Right - Experience Section */}
          <div className="bg-card rounded-2xl p-6 shadow-lg">
            <h3 className="text-xl font-bold text-foreground mb-4">
              La Sagesse de l'Expérience
            </h3>
            <p className="text-sm text-muted-foreground leading-relaxed">
              Plusieurs décennies d'engagement et de confiance. 
              Une institution au service de ses membres.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default TeamSection;