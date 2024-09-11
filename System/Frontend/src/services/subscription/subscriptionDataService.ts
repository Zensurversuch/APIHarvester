import { INFLUX_API_BASE_URL } from "../apiConfig";

export const subscriptionData = async (token: string, subscriptionID: number, timespan: number): Promise<any> => {
  try {
    const response = await fetch(`${INFLUX_API_BASE_URL}influxGetData/${subscriptionID}/${timespan}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorMessage = await response.text();
      throw new Error(`Failed to fetch data: ${errorMessage}`);
    }

    const result = await response.json();
    return result;

  } catch {
      throw new Error('Fetching subscription data failed. Please try again later.');
  }
};
