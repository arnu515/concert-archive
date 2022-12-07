import { sveltekit } from '@sveltejs/kit/vite';
import type { UserConfig } from 'vite';

const config: UserConfig = {
	plugins: [sveltekit()],
	server: {
		port: 3000,
		proxy: {
			'/api': {
				target: 'http://0.0.0.0:5000',
				changeOrigin: true
			}
		}
	}
};

export default config;
