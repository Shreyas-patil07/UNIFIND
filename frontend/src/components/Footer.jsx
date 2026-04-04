import React from 'react';

const Footer = () => {
  return (
    <footer className="py-12 px-6 sm:px-8 md:px-12 lg:px-24 bg-slate-900 text-slate-400">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          {/* Brand */}
          <div>
            <div className="font-['Outfit'] font-black text-2xl text-white mb-4">UNIFIND</div>
            <p className="text-sm">
              AI-powered student-to-student marketplace for campus commerce.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-white font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2 text-sm">
              <li><a href="/" className="hover:text-blue-400 transition-colors">Home</a></li>
              <li><a href="/buyer" className="hover:text-blue-400 transition-colors">Browse</a></li>
              <li><a href="/seller" className="hover:text-blue-400 transition-colors">Sell</a></li>
              <li><a href="/home" className="hover:text-blue-400 transition-colors">Dashboard</a></li>
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-white font-semibold mb-4">Contact</h3>
            <p className="text-sm mb-2">systemrecord07@gmail.com</p>
            <a 
              href="https://github.com/Shreyas-patil07/UniFind" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-sm hover:text-blue-400 transition-colors"
            >
              GitHub Repository
            </a>
          </div>
        </div>

        <div className="border-t border-slate-700 pt-6 text-center text-sm">
          <p>© 2026 UNIFIND. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
