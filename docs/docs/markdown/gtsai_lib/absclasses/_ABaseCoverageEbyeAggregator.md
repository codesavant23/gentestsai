# Abstract class `_ABaseCoverageEbyeAggregator`
Represents a base `ICoveragePyEbyeAggregator`, containing the control logic
common to every `ICoveragePyEbyeAggregator`.


!!! ext-points "Extension Points"
	
	- The format of the "coverage.py" report being processed is specified by the
	
	- descendants of this abstract class
	

!!! abstract "Details"
	- **Fully-qualified Name**: `calc_coverage.covpy_ebye_aggr._ABaseCoverageEbyeAggregator`
	
    - **Inherits from:**
		
		- ICoveragePyEbyeAggregator
		
	
	


## Public methods

- [**add_exclusion**](../methods/_ABaseCoverageEbyeAggregator/add_exclusion.md) `(self, excl_entity: str, pass_onerror: bool = False)`

- [**rem_exclusion**](../methods/_ABaseCoverageEbyeAggregator/rem_exclusion.md) `(self, excl_entity: str, pass_onerror: bool = False)`

- [**aggregate**](../methods/_ABaseCoverageEbyeAggregator/aggregate.md) `( self, report_path: str, focal_root: str, aggr_path: str )`

- [**_ap__assert_report_type**](../methods/_ABaseCoverageEbyeAggregator/_ap__assert_report_type.md) `(self, report_path: str)`

- [**_ap__aggregate_spec**](../methods/_ABaseCoverageEbyeAggregator/_ap__aggregate_spec.md) `( self, report_path: str, focal_root: str, aggr_path: str, exclusions: Set[str] )`


