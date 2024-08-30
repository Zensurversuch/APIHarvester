import React from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Row, Col, Button } from 'react-bootstrap';
import logo from '../../assets/API_Harvester_Logo.jpeg';

const Home: React.FC = () => {
    const { t } = useTranslation();

    return (
        <Container className="text-center mt-5">
            <Row>
                <Col>
                    <h1>{t('welcomeMessage')}</h1>
                    <p className="lead mt-3">{t('appDescription')}</p>
                    <Button
                        variant="primary"
                        className="mt-3"
                        href="https://github.com/Zensurversuch/APIHarvester"
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        {t('learnMore')}
                    </Button>
                    <div className="mt-3">
                        <img
                            src={logo}
                            alt="API Harvester Logo"
                            className="img-fluid"
                            style={{ maxWidth: '50%' }}
                        />
                    </div>
                </Col>
            </Row>
        </Container>
    );
};

export default Home;
