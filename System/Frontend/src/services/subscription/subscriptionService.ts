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

// Fetch subscriptionsByUserID endpoint
export const fetchSubscriptions = async (token: string, userID: string) => {
  try {
    const response = await fetch(`${POSTGRES_API_BASE_URL}subscriptionsByUserID/${userID}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,  
        'Content-Type': 'application/json',
      },
    }
    );
    if (!response.ok) throw new Error('Failed to fetch subscriptions');
    return response.json() as Promise<Subscription[]>;
  } catch (error) {
    throw error;
  }
};

// Fetch subscribeApi endpoint
export const subscribe = async (token: string, userID: string, apiID: number, interval: number): Promise<string> => {
  try {
    const response = await fetch(`${SCHEDULER_API_BASE_URL}subscribeApi`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,  
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

// Fetch resubscribeApi endpoint
export const resubscribe = async (token: string, subscriptionID: number): Promise<string> => {
  try {
    const response = await fetch(`${SCHEDULER_API_BASE_URL}resubscribeApi/${subscriptionID}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,  
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


// Fetch unsubscribeApi endpoint
export const unsubscribe = async (token: string, subscriptionID: number) => {
  try {
    const response = await fetch(`${SCHEDULER_API_BASE_URL}/unsubscribeApi/${subscriptionID}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,  
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) throw new Error('Failed to remove subscription');
    return response.json();
  } catch {
    throw new Error('Unsubscribing failed due to an error. Please try again later.'); 
  }
};
