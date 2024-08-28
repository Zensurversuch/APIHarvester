import React from 'react';
import { useTranslation } from 'react-i18next';
import { Navbar, Nav, Container } from 'react-bootstrap';

const Header: React.FC = () => {
  const { t } = useTranslation();

  return (
    <Navbar bg="dark" variant="dark" expand="lg" sticky="top">
      <Container>
        <Navbar.Brand href="/">{t('appName')}</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ml-auto">
            <Nav.Link href="/">{t('navHome')}</Nav.Link>
            <Nav.Link href="/login">{t('navLogin')}</Nav.Link>
            <Nav.Link href="/apis">{t('apiListTitle')}</Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Header;
