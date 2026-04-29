import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  // GitHub Pages serves from /bigknoxy.github.io/auto-portfolio/
  // Setting `base` fixes all asset/CSS paths
  site: 'https://bigknoxy.github.io',
  base: '/auto-portfolio',
  integrations: [tailwind()],
  output: 'static',
  build: {
    assets: 'assets',
  },
});
