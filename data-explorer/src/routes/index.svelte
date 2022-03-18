<script lang="ts">
	import AgGrid from "@budibase/svelte-ag-grid";

	let data = [
		{ make: "Toyota", model: "Celica", price: 35000 },
		{ make: "Ford", model: "Mondeo", price: 32000 },
		{ make: "Porsche", model: "Boxter", price: 72000 },
	];

	let columnDefs = [
		{
			headerName: "Make",
			field: "make",
			sortable: true,
			editable: true,
		},
		{ headerName: "Model", field: "model", sortable: true },
		{ headerName: "Price", field: "price", sortable: true },
	];
</script>

<style>
    :global(:root) {
        --grid-height: 500px;
    }
</style>

<AgGrid bind:data {columnDefs} />