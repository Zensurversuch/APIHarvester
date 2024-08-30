import { POSTGRES_API_BASE_URL, SCHEDULER_API_BASE_URL } from '../apiConfig';

export interface Subscription {
  availableApiID: number;
  interval: number;
  status: 'ACTIVE' | 'INACTIVE';
  subscriptionID: number;
  userID: number;
  jobName: string;
  container: string;
}

export const fetchSubscriptions = async (userID: string) => {
  try {
    const response = await fetch(`${POSTGRES_API_BASE_URL}subscriptionsByUserID/${userID}`);
    if (!response.ok) throw new Error('Failed to fetch subscriptions');
    return response.json() as Promise<Subscription[]>;
  } catch (error) {
    throw error;
  }
};

export const subscribe = async (userID: string, apiID: number, interval: number): Promise<string> => {
  try {
    const response = await fetch(`${SCHEDULER_API_BASE_URL}subscribeApi`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        userID: userID,
        apiID: apiID,
        interval: interval
      }),
    });

    if (!response.ok) {
      const errorMessage = await response.text(); 
      throw new Error(`Subscription failed: ${errorMessage}`); 
    }
    return 'Subscription successful!'; 
  } catch {
    throw new Error('Subscribing failed due to an error. Please try again later.'); 
  }
};

export const resubscribe = async (subscriptionID: number): Promise<string> => {
  try {
    const response = await fetch(`${SCHEDULER_API_BASE_URL}resubscribeApi/${subscriptionID}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorMessage = await response.text(); 
      throw new Error(`Subscription failed: ${errorMessage}`); 
    }
    return 'Activate subscription successful!'; 
  } catch {
    throw new Error('Resubscribing failed due to an error. Please try again later.'); 
  }
};



export const unsubscribe = async (subscriptionID: number) => {
  try {
    const response = await fetch(`${SCHEDULER_API_BASE_URL}/unsubscribeApi/${subscriptionID}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) throw new Error('Failed to remove subscription');
    return response.json();
  } catch {
    throw new Error('Unsubscribing failed due to an error. Please try again later.'); 
  }
};
