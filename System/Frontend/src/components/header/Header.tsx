import React from 'react';
import { useTranslation } from 'react-i18next';
import { Navbar, Nav, Container, Button } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';

const Header: React.FC = () => {
  const { t } = useTranslation();
  const { isLoggedIn, clearAuth } = useAuth();

  const handleLogout = () => {
    clearAuth(); // Clear authentication data
  };

  return (
    <Navbar bg="dark" variant="dark" expand="lg" sticky="top">
      <Container fluid> {/* Use Container fluid to span the full width */}
        <Navbar.Brand href="/">{t('appName')}</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav" className="justify-content-between">
          <Nav>
            <Nav.Link href="/">{t('navHome')}</Nav.Link>
            <Nav.Link href="/apis">{t('apiListTitle')}</Nav.Link>
          </Nav>
          <Nav>
            {isLoggedIn() ? (
              <Button variant="outline-light" onClick={handleLogout}>
                {t('navLogout')}
              </Button>
            ) : (
              <Button variant="outline-light" href="/login">
                {t('navLogin')}
              </Button>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Header;
