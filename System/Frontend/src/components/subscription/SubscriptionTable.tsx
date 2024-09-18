import React, { useEffect, useState } from 'react';
import { Button, Table, Modal, Spinner, Alert } from 'react-bootstrap';
import { useAuth } from '../../contexts/AuthContext';
import { fetchSubscriptions, Subscription, unsubscribe, resubscribe } from '../../services/subscription/subscriptionService';
import { useAPI, ApiData } from '../../contexts/ApiDataContext';
import StatusMessage from '../util/StatusMessage';
import { useNavigate } from 'react-router-dom';

const SubscriptionTable: React.FC = () => {
  const { userID, getAndCheckToken } = useAuth();
  const { apiData, loading: apiLoading, error: apiError } = useAPI();
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedApi, setSelectedApi] = useState<ApiData | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [statusType, setStatusType] = useState<'success' | 'failure'>('success');
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const navigate = useNavigate();

  // Load Subscription from backend
  const loadSubscriptions = async () => {
    if (userID) {
      setLoading(true);
      setError(null);
      try {
        const data = await fetchSubscriptions(getAndCheckToken(), userID);
        setSubscriptions(data);
      } catch (err) {
        setError('Failed to fetch subscriptions');
      } finally {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    loadSubscriptions();
  }, [userID]);

  // Combine subscriptions with API data
  const combinedData = subscriptions.map((sub) => ({
    subscription: sub,
    api: apiData.find(api => api.availableApiID === sub.availableApiID)
  }));

  // Opens the API details modal and not the fetch data site
  const handleApiNameClick = (api: ApiData, e: React.MouseEvent) => {
    e.stopPropagation();
    setSelectedApi(api);
    setShowModal(true);
  };

  // Close the API details modal
  const handleCloseModal = () => {
    setShowModal(false);
    setSelectedApi(null);
  };

  // Navigate to the DisplayData page by table Row click
  const handleRowClick = (subscriptionID: number, apiID: number) => {
    navigate(`/subscriptionData/${subscriptionID}/${apiID}`); 
  };

  // Resubscribe an inactive API subscription
  const handleSubscribe = async (subscriptionID: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await resubscribe(getAndCheckToken(), subscriptionID);
      setStatusMessage('Resubscription successful!');
      setStatusType('success');
      const data = await fetchSubscriptions(getAndCheckToken(), userID);
      setSubscriptions(data);
    } catch (error) {
      setStatusMessage('Failed to resubscribe.');
      setStatusType('failure');
    }
  };

  // Unsubscribe an active API subscription
  const handleUnsubscribe = async (subscriptionID: number, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await unsubscribe(getAndCheckToken(), subscriptionID);
      setStatusMessage('Unsubscription successful!');
      setStatusType('success');
      loadSubscriptions();
    } catch (error) {
      if (error instanceof Error) {
        setStatusMessage(error.message);
      } else {
        setStatusMessage('An unknown error occurred.');
      }
      setStatusType('failure');
    }
  };

  // Sort handling logic
  const handleSort = (column: string) => {
    if (['subscriptionID', 'container', 'status'].includes(column)) {
      const direction = sortColumn === column && sortDirection === 'asc' ? 'desc' : 'asc';
      setSortColumn(column);
      setSortDirection(direction);

      const sortedData = [...combinedData].sort((a, b) => {
        const aValue = a.subscription[column as keyof Subscription];
        const bValue = b.subscription[column as keyof Subscription];

        // Determine if the values should be treated as numbers or strings
        const isNumeric = !isNaN(Number(aValue)) && !isNaN(Number(bValue));

        if (isNumeric) {
          // Handle numeric sorting
          const numA = Number(aValue);
          const numB = Number(bValue);
          return direction === 'asc' ? numA - numB : numB - numA;
        } else {
          // Handle string sorting
          if (aValue < bValue) return direction === 'asc' ? -1 : 1;
          if (aValue > bValue) return direction === 'asc' ? 1 : -1;
          return 0;
        }
      });

      setSubscriptions(sortedData.map(item => item.subscription));  // Update subscriptions
    }
  };

  if (loading || apiLoading) return (
    <div className="text-center mt-5">
      <Spinner animation="border" role="status">
        <span className="visually-hidden">Loading...</span>
      </Spinner>
    </div>
  );

  if (error || apiError) return (
    <div className="text-center mt-5">
      <Alert variant="danger">{error || apiError}</Alert>
    </div>
  );

  return (
    <>
      {statusMessage && (
        <StatusMessage 
          message={statusMessage}
          type={statusType}
          onClose={() => setStatusMessage(null)} // Clear message on close
        />
      )}
      <div className="mb-4" style={{ width: '50%', margin: '0 auto' }}>
        <Alert variant="info" className="text-center" style={{ margin: 0 }}>
          <p style={{ margin: 0 }}>
            <strong>Information:</strong>
          </p>
          <p style={{ margin: 0 }}>
            <span>&#8226;</span> Click on a column header to sort the data.
          </p>
          <p style={{ margin: 0 }}>
            <span>&#8226;</span> Clicking on "API Name" will show detailed information about the API.
          </p>
          <p style={{ margin: 0 }}>
            <span>&#8226;</span> Click on a row to view data collected by the subscription.
          </p>
        </Alert>
      </div>


      <Table striped bordered hover>
        <thead>
          <tr>
            <th onClick={() => handleSort('subscriptionID')}>
              Subscription ID {sortColumn === 'subscriptionID' ? (sortDirection === 'asc' ? '▲' : '▼') : '⇅'}
            </th>
            <th>
              API Name
            </th>
            <th>
              Interval
            </th>
            <th>
              Job Name
            </th>
            <th onClick={() => handleSort('container')}>
              Executing Container {sortColumn === 'container' ? (sortDirection === 'asc' ? '▲' : '▼') : '⇅'}
            </th>
            <th onClick={() => handleSort('status')}>
              Status {sortColumn === 'status' ? (sortDirection === 'asc' ? '▲' : '▼') : '⇅'}
            </th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {combinedData.map(({ subscription, api }) => (
            <tr 
              key={subscription.subscriptionID}
              onClick={() => handleRowClick(subscription.subscriptionID, api?.availableApiID || 0)}
              style={{ cursor: 'pointer' }}
            >
              <td>{subscription.subscriptionID}</td>
              <td>
                {api ? (
                  <Button
                    variant="link"
                    onClick={(e) => handleApiNameClick(api, e)}
                  >
                    {api.name}
                  </Button>
                ) : (
                  'Unknown API'
                )}
              </td>
              <td>{subscription.interval} seconds</td>
              <td>{subscription.jobName}</td>
              <td>{subscription.container}</td>
              <td style={{
                  color: subscription.status === 'ACTIVE' ? 'green' :
                        subscription.status === 'INACTIVE' ? 'orange' :
                        subscription.status === 'ERROR' ? 'red' : 'black'
                  }}>
                {subscription.status}
              </td>
              <td>
                {subscription.status === 'ACTIVE' && (
                  <Button
                    variant="danger"
                    onClick={(e) => handleUnsubscribe(subscription.subscriptionID, e)}
                  >
                    Unsubscribe
                  </Button>
                )}
                {subscription.status === 'INACTIVE' && (
                  <Button
                    variant="primary"
                    onClick={(e) => handleSubscribe(subscription.subscriptionID, e)}
                  >
                    Subscribe
                  </Button>
                )}
                {subscription.status !== 'ACTIVE' && subscription.status !== 'INACTIVE' && (
                <Button
                  variant="secondary"
                  onClick={(e) => {
                    e.stopPropagation();
                    window.location.href = `mailto:apiharvester@gmail.com?subject=Help%20Request&body=Please%20describe%20your%20issue%20with%20subscription%20${subscription.subscriptionID}%20here.`;}
                  }>
                  Help
                </Button>             
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </Table>

      <Modal show={showModal} onHide={handleCloseModal}>
        <Modal.Header closeButton>
          <Modal.Title>API Details</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedApi ? (
            <div>
              <h5>{selectedApi.name}</h5>
              <p><strong>ID:</strong> {selectedApi.availableApiID}</p>
              <p><strong>Description:</strong> {selectedApi.description}</p>
              {/* Add any other details you want to display about the API */}
            </div>
          ) : (
            <p>No API details available.</p>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCloseModal}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default SubscriptionTable;
