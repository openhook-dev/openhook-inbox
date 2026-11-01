import { hydrateRoot } from 'react-dom/client';
import { Home } from './Home';
const root = document.getElementById('home-root');
if (root) hydrateRoot(root, <Home origin={root.dataset.origin!} />);
