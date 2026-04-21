export default {
  '*.{ts,tsx}': ['npm run lint:fix', 'npm run format'],
  '*.{html,css,json}': 'npm run format',
};
