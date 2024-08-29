import React from 'react';
import { Card, Container, Row, Col, Spinner, Alert } from 'react-bootstrap';
import { useAPI } from '../../contexts/ApiDataContext';

const APIList: React.FC = () => {
  const { apiData, loading, error } = useAPI();

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="text-center mt-5">
        <Alert variant="danger">{error}</Alert>
      </Container>
    );
  }

  return (
    <Container className="mt-5">
      <Row>
        {apiData.map(api => (
          <Col key={api.availableApiID} md={6} lg={4}>
            <Card className="mb-4">
              <Card.Body>
                <Card.Title>{api.description}</Card.Title>
                <Card.Text>
                  <strong>Subscription Type:</strong> {api.subscriptionType}
                </Card.Text>
                <Card.Text>
                  <strong>Relevant Fields:</strong> {api.relevantFields.join(', ')}
                </Card.Text>
                <Card.Text>
                  <strong>URL: </strong>{api.url}
                </Card.Text>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
};

export default APIList;
