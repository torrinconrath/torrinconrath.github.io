import Column from "./Column.js";

export default class Kanban {
	constructor(root) {
		this.root = root;

		Kanban.columns().forEach(column => {
			const columnView = new Column(column.id, column.title);

			this.root.appendChild(columnView.elements.root);
		});
	}

	static columns() {
		return [
			{
				id: 1,
				title: "Not Started"
			},
			{
				id: 2,
				title: "In Progress"
			},
			{
				id: 3,
				title: "Completed"
			}
		];
	}

	static setBackgroundImage(url) {
		const image = new Image();
		image.src = url;
		image.onload = () => {
		  document.body.style.backgroundImage = `url(${url})`;
		  document.body.style.backgroundSize = "cover";
		};
	  }
}
