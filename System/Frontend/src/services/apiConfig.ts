import constants from '../commonRessources/constants.json';

// Load backend URLs from constants
export const POSTGRES_API_BASE_URL = constants.POSTGRES_DATA_CONNECTOR_URL + '/';
export const INFLUX_API_BASE_URL = constants.INFLUX_DATA_CONNECTOR_URL + '/';
export const SCHEDULER_API_BASE_URL = constants.SCHEDULER_API_URL + '/';