import React from 'react';
import './Footer.css';

function Footer() {
  return (
    <footer className="footer">
      <div>
        &copy; {new Date().getFullYear()} Shoppable.AI. All rights reserved.
      </div>
      <div className="footer-dev">
        <strong>Team3</strong> | github: <a href="mailto:your.email@example.com">https://github.com/Capstone-Design-with-Google/Capstone-Design-Team3</a>
      </div>
    </footer>
  );
}

export default Footer;
