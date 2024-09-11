import { useAuth } from "../../contexts/AuthContext";
import { INFLUX_API_BASE_URL } from "../apiConfig";

export const subscriptionData = async (subscriptionID: number, timespan: number): Promise<any> => {
  try {
    const {getAndCheckToken} = useAuth();
    const response = await fetch(`${INFLUX_API_BASE_URL}influxGetData/${subscriptionID}/${timespan}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${getAndCheckToken}`,
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
