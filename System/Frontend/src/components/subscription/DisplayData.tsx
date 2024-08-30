import React, { useState, useEffect } from 'react';
import { Table, Form, Spinner, Alert, Button } from 'react-bootstrap';
import { useAPI, ApiData } from '../../contexts/ApiDataContext';
import { subscriptionData } from '../../services/subscription/subscriptionDataService';
import { useParams, useNavigate } from 'react-router-dom';

interface DataPoint {
  _measurement: string;
  _start: string;
  _stop: string;
  _time: string;
  fetchTimestamp: string;
  result: string;
  subscriptionID: number;
  table: number;
  value: string;
}

const DisplayData: React.FC = () => {
  const { subscriptionID: subscriptionIDString, apiID: apiIDString } = useParams<{ subscriptionID: string; apiID: string }>();
  const subscriptionID = Number(subscriptionIDString);
  const apiID = Number(apiIDString);
  const { apiData, loading: apiLoading, error: apiError } = useAPI();
  const [data, setData] = useState<DataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timespan, setTimespan] = useState<number>(60);
  const [timespanError, setTimespanError] = useState<string | null>(null);

  const navigate = useNavigate();
  const selectedApi = apiData.find((api: ApiData) => api.availableApiID === apiID);

  const fetchData = async () => {
    if (!selectedApi) {
        setError('API not found');
        setLoading(false);
        return;
      }
      
    try {
      const response = await subscriptionData(subscriptionID, timespan);
      setData(response);
    } catch (error) {
      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError('An unknown error occurred. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!apiLoading) {
        fetchData();
      }
    }, [selectedApi, timespan, subscriptionID, apiLoading]);

  const handleTimespanChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = Number(e.target.value);
    if (value < 1) {
      setTimespanError('Timespan must be at least 1 minute.');
    } else if (value > 518400) {
      setTimespanError('Timespan must not exceed 518,400 minutes (360 days).');
    } else {
      setTimespanError(null);
      setTimespan(value);
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

  // Parse the JSON strings in 'value'
  const parsedData = data.map(point => ({
    ...point,
    value: JSON.parse(point.value),
  }));

  return (
    <div>
      <div className="d-flex justify-content-between mb-3">
        <Button variant="secondary" onClick={() => navigate(-1)}>
          Go Back
        </Button>
        <Button variant="primary" onClick={fetchData}>
          Refresh
        </Button>
      </div>

      <Form.Group controlId="timespanControl">
        <Form.Label>Select Timespan (minutes)</Form.Label>
        <Form.Control
          type="number"
          value={timespan}
          onChange={handleTimespanChange}
        />
        {timespanError && (
            <div className="text-center mb-3">
                <Alert variant="warning">{timespanError}</Alert>
            </div>
        )}
      </Form.Group>

      {data.length === 0 ? (
        <div className="text-center mb-3">
            <Alert variant="info">No data available for the selected timespan. Please adjust the timespan or check back later.</Alert>
        </div>
      ) : (
        <Table striped bordered hover>
          <thead>
            <tr>
              <th>Time</th>
              {selectedApi?.relevantFields.map(field => (
                <th key={field}>{field}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {parsedData.map((point, index) => (
              <tr key={index}>
                <td>{new Date(point._time).toLocaleString()}</td>
                {selectedApi?.relevantFields.map(field => (
                  <td key={field}>{point.value[field] || 'N/A'}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </Table>
      )}
    </div>
  );
};

export default DisplayData;
