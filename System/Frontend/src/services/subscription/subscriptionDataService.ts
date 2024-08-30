import { INFLUX_API_BASE_URL } from "../apiConfig";

export const subscriptionData = async (subscriptionID: number, timespan: number): Promise<any> => {
  try {
    const response = await fetch(`${INFLUX_API_BASE_URL}influxGetData/${subscriptionID}/${timespan}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorMessage = await response.text();
      console.error('Failed to fetch subscription data:', errorMessage);
      throw new Error(`Failed to fetch data: ${errorMessage}`);
    }

    const result = await response.json();
    return result;

  } catch (error) {
      throw new Error('Fetching subscription data failed. Please try again later.');
  }
};
