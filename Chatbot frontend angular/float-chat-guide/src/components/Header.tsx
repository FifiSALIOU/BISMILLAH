import { Button } from '@/components/ui/button';

const Header = () => {
  return (
    <>
      {/* Top orange bar */}
      <div className="bg-orange-500 text-white px-6 py-2">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="font-bold text-lg">CSS - IPRES</span>
          </div>
          <div className="flex items-center gap-6 text-sm">
            <Button variant="ghost" className="text-white hover:text-orange-200 p-0 h-auto font-normal">
              Accueil
            </Button>
            <Button variant="ghost" className="text-white hover:text-orange-200 p-0 h-auto font-normal">
              Qui sommes-nous ?
            </Button>
            <Button variant="ghost" className="text-white hover:text-orange-200 p-0 h-auto font-normal">
              Actualité
            </Button>
            <Button variant="ghost" className="text-white hover:text-orange-200 p-0 h-auto font-normal">
              Contact
            </Button>
          </div>
        </div>
      </div>
      
      {/* Second navigation bar */}
      <div className="bg-gray-200 px-6 py-3">
        <div className="container mx-auto flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Button variant="ghost" className="text-gray-700 hover:text-gray-900 p-0 h-auto font-medium">
              EMPLOYEUR
            </Button>
            <Button variant="ghost" className="text-gray-700 hover:text-gray-900 p-0 h-auto font-medium">
              SALARIE
            </Button>
            <Button variant="ghost" className="text-gray-700 hover:text-gray-900 p-0 h-auto font-medium">
              ALLOCATAIRE
            </Button>
          </div>
          <div className="flex items-center gap-4">
            <Button variant="ghost" className="text-white bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded">
              Connexion
            </Button>
            <Button variant="ghost" className="text-white bg-gray-800 hover:bg-gray-900 px-4 py-2 rounded">
              S'inscrire
            </Button>
          </div>
        </div>
      </div>
      
      {/* Logo section */}
       <div className="bg-white px-6 py-4 border-b">
         <div className="container mx-auto flex items-center">
           <div className="flex items-center">
             <img 
               src="/lovable-uploads/logo.png" 
               alt="Caisse de Sécurité Sociale IPRES" 
               className="h-16 w-auto"
             />
           </div>
         </div>
       </div>
    </>
  );
};

export default Header;