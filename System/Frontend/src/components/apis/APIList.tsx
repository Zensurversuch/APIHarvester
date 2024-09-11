import React, { useState } from 'react';
import { Card, Container, Row, Col, Spinner, Alert, Button, Modal, Form } from 'react-bootstrap';
import { ApiData, useAPI } from '../../contexts/ApiDataContext';
import { subscribe } from '../../services/subscription/subscriptionService';
import { useAuth } from '../../contexts/AuthContext';
import StatusMessage from '../util/StatusMessage';

const ApiList: React.FC = () => {
  const { userID, getAndCheckToken } = useAuth();
  const { apiData, loading, error } = useAPI();
  const [showModal, setShowModal] = useState(false);
  const [selectedApi, setSelectedApi] = useState<ApiData | null>(null);
  const [interval, setInterval] = useState<string>('60');
  const [customInterval, setCustomInterval] = useState<string>('');
  const [inputError, setInputError] = useState<string>('');

  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [statusType, setStatusType] = useState<'success' | 'failure'>('success');

  const handleSubscribeClick = (api: ApiData) => {
    setSelectedApi(api);
    setShowModal(true);
  };

  const handleClose = () => {
    setShowModal(false);
    setInterval('60');
    setCustomInterval('');
    setInputError('');
  };

  const handleSubscribe = async () => {
    const maxInt32 = 2147483647;
    let intervalNumber: number;

    if (interval === 'custom') {
      intervalNumber = parseInt(customInterval, 10);
      if (isNaN(intervalNumber) || intervalNumber <= 0) {
        setInputError('Please enter a valid positive integer for custom interval.');
        return;
      } else if (intervalNumber > maxInt32) {
        setInputError(`Interval cannot exceed ${maxInt32} seconds.`);
        return;
      }
    } else {
      intervalNumber = parseInt(interval, 10);
      if (isNaN(intervalNumber) || intervalNumber <= 0) {
        setInputError('Please enter a valid positive integer for interval.');
        return;
      } else if (intervalNumber > maxInt32) {
        setInputError(`Interval cannot exceed ${maxInt32} seconds.`);
        return;
      }
    }

    if (selectedApi?.availableApiID !== undefined) {
      try {
        await subscribe(getAndCheckToken(), userID, selectedApi.availableApiID, intervalNumber);
        setStatusMessage('Subscription successful!');
        setStatusType('success');
      } catch (error) {
        if (error instanceof Error) {
          setStatusMessage(error.message);
        } else {
          setStatusMessage('An unknown error occurred.');
        }
        setStatusType('failure');
      }
    } else {
      setStatusMessage('API ID is undefined.');
      setStatusType('failure');
    }

    handleClose();
  };

  // Ensure your component returns a valid ReactNode
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
            <Card className="mb-4 h-100">
              <Card.Body>
                <Card.Title>{api.name}</Card.Title>
                <Card.Text>
                  {api.description}
                </Card.Text>
                <Card.Text>
                  <strong>Subscription Type:</strong> {api.subscriptionType}
                </Card.Text>
              </Card.Body>
              <Card.Footer>
                <Button
                  variant="primary"
                  onClick={() => handleSubscribeClick(api)}
                  className="w-100"
                >
                  Subscribe
                </Button>
              </Card.Footer>
            </Card>
          </Col>
        ))}
      </Row>

      {statusMessage && (
        <StatusMessage 
          message={statusMessage}
          type={statusType}
          onClose={() => setStatusMessage('')} 
        />
      )}

      <Modal show={showModal} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>Subscribe to {selectedApi?.name}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group controlId="subscriptionInterval">
              <Form.Label>Select Subscription Interval</Form.Label>
              <Form.Control
                as="select"
                value={interval}
                onChange={(e) => {
                  setInterval(e.target.value);
                  if (e.target.value !== 'custom') {
                    setCustomInterval('');
                  }
                  setInputError('');
                }}
              >
                <option value="60">1 minute</option>
                <option value="180">3 minutes</option>
                <option value="300">5 minutes</option>
                <option value="600">10 minutes</option>
                <option value="custom">Custom (in seconds)</option>
              </Form.Control>
            </Form.Group>

            {interval === 'custom' && (
              <Form.Group controlId="customInterval" className="mt-3">
                <Form.Label>Enter Custom Interval (seconds)</Form.Label>
                <Form.Control
                  type="number"
                  placeholder="Enter interval in seconds"
                  value={customInterval}
                  onChange={(e) => {
                    setCustomInterval(e.target.value);
                    setInputError('');
                  }}
                  min="1"
                  isInvalid={!!inputError}
                />
                <Form.Control.Feedback type="invalid">
                  {inputError}
                </Form.Control.Feedback>
              </Form.Group>
            )}
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleSubscribe}>
            Subscribe
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
};

export default ApiList;
