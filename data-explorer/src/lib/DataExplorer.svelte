<script lang="ts">

    import DataGrid from "./DataGrid.svelte";
    import LifetimeInput from "./LifetimeInput.svelte";
    import RegionPicker from "./RegionPicker.svelte";
    import RequestButton from "./RequestButton.svelte";

    let datagrid;
    let lifetime;
    let region;
    let disabledSearchButton;

</script>
<div>
<LifetimeInput bind:lifetime/>
<RegionPicker bind:region/>
<RequestButton bind:disabledSearchButton/>
<DataGrid bind:datagrid/>
</div>
