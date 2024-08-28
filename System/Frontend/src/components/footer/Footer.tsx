import React from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Row, Col } from 'react-bootstrap';

const Footer: React.FC = () => {
  const { t } = useTranslation();

  return (
    <footer className="bg-dark text-white mt-5 p-4 text-center">
      <Container>
        <Row>
          <Col md="12">
            <p className="mb-0">&copy; 2024 {t('appName')}</p>
          </Col>
        </Row>
      </Container>
    </footer>
  );
};

export default Footer;
