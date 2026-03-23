import Alpine from 'alpinejs';

import { getApiBaseUrl } from './lib/api';
import './styles.css';

Alpine.data('appShell', () => ({
  apiBaseUrl: `API: ${getApiBaseUrl()}`,
}));

window.Alpine = Alpine;
Alpine.start();
