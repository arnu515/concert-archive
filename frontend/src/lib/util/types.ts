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

export interface ChatMessage {
	id: string;
	type: 'TEXT' | 'FILE' | 'EVENT';
	message_data: string;
	stage_id: string;
	user_id: string;
	created_at: string;
	updated_at: string;
	stage: Stage;
	user: User;
}
