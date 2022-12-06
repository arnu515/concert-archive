export interface User {
	id: string;
	email: string;
	username: string;
	avatar_url: string;
	created_at: string;
}

export interface Stage {
	name: string;
	private: boolean;
	owner: User;
	id: string;
	owner_id: string;
	color: string;
}
