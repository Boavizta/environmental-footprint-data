import adapter from '@sveltejs/adapter-auto';
import preprocess from 'svelte-preprocess';
import * as path from 'path';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: preprocess(),

	kit: {
		adapter: adapter(),
		vite: {
			optimizeDeps: {
				include: ['@budibase/svelte-ag-grid']
			},
			resolve: {
				alias: {
					$: path.resolve('./src/')
				}
			}
		}
	}
};

export default config;
