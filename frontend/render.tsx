import { writeFileSync } from 'node:fs';
import { renderToString } from 'react-dom/server';
import { Home } from './Home';
const html = renderToString(<Home origin="{{origin}}" />);
writeFileSync('web/pages/home.html', `<div id="home-root" data-origin="{{origin}}">${html}</div>\n`);
