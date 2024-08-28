import React from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Row, Col, Button } from 'react-bootstrap';

const Home: React.FC = () => {
    const { t } = useTranslation();

  return (
    <Container className="text-center mt-5">
      <Row>
        <Col>
          <h1>{t('welcomeMessage')}</h1>
          <p className="lead mt-3">{t('appDescription')}</p>
          <Button variant="primary" className="mt-3" href="https://github.com/Zensurversuch/APIHarvester" target="_blank" rel="noopener noreferrer">
            {t('learnMore')}
          </Button>
        </Col>
      </Row>
    </Container>
  );
};

export default Home;