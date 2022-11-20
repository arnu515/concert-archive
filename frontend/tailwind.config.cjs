const config = {
	content: ['./src/**/*.{html,js,svelte,ts}'],

	theme: {
		extend: {}
	},

	plugins: [require('daisyui')],

	daisyui: {
		themes: [
			{
				concert: {
					primary: '#00A9A5',
					secondary: '#3E5C76',
					accent: '#cc3363',
					neutral: '#191D24',
					'base-100': '#242331',
					info: '#3ABFF8',
					success: '#85FF9E',
					warning: '#F6AA1C',
					error: '#AC3931'
				}
			}
		]
	}
};

module.exports = config;
