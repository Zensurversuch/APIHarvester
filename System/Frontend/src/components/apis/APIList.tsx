import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Container, Row, Col, Table, Button, Collapse } from 'react-bootstrap';

// Define the API data structure
interface API {
  name: string;
  description: string;
  endpoint: string;
  additionalInfo?: string; // Optional field for more details
}

interface APIListProps {
  apiData: API[];
}

const APIList: React.FC<APIListProps> = ({ apiData }) => {
  const { t } = useTranslation();
  const [open, setOpen] = useState<string | null>(null);

  const handleToggle = (name: string) => {
    setOpen(open === name ? null : name);
  };

  return (
    <Container className="mt-5">
      <Row>
        <Col>
          <h1>{t('apiListTitle')}</h1>
          <Table striped bordered hover>
            <thead>
              <tr>
                <th>{t('apiName')}</th>
                <th>{t('apiDescription')}</th>
                <th>{t('apiEndpoint')}</th>
                <th>{t('details')}</th>
              </tr>
            </thead>
            <tbody>
              {apiData.map((api) => (
                <React.Fragment key={api.name}>
                  <tr>
                    <td>{api.name}</td>
                    <td>{api.description}</td>
                    <td>{api.endpoint}</td>
                    <td>
                      <Button
                        variant="info"
                        onClick={() => handleToggle(api.name)}
                      >
                        {open === api.name ? t('hideDetails') : t('showDetails')}
                      </Button>
                    </td>
                  </tr>
                  <tr>
                    <td colSpan={4}>
                      <Collapse in={open === api.name}>
                        <div>
                          {api.additionalInfo && (
                            <>
                              <p><strong>{t('apiDetails')}</strong></p>
                              <p>{api.additionalInfo}</p>
                            </>
                          )}
                        </div>
                      </Collapse>
                    </td>
                  </tr>
                </React.Fragment>
              ))}
            </tbody>
          </Table>
        </Col>
      </Row>
    </Container>
  );
};

export default APIList;