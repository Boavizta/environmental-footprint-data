<script lang="ts">

    import DataGrid from "./DataGrid.svelte";
    import LifetimeInput from "./LifetimeInput.svelte";
    import RegionPicker from "./RegionPicker.svelte";
    import RequestButton from "./RequestButton.svelte";
    import EquivalentImpacts from "./EquivalentImpacts.svelte";

    let datagrid;
    let lifetime;
    let region;
    let disabledSearchButton;

</script>
<div>
<DataGrid bind:datagrid/>
<RegionPicker bind:region/>
<LifetimeInput bind:lifetime/>
<RequestButton bind:disabledSearchButton/>
<EquivalentImpacts gwpImpactTotal="200"/>
</div>
