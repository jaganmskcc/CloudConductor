# Glossary

<dl>
  <dt> Run </dt>
  <dd> A completed, successful or failed, execution of a pipeline using CloudConductor. </dd>

  <dt> Pipeline </dt>
  <dd> A directed graph or bioinformatics tools that are executed in a certain order. </dd>

  <dt> Graph </dt>
  <dd> Synonym for Pipeline</dd>

  <dt> Module </dt>
  <dd> Node of a Pipeline graph. It can be a bioinformatics tool, a splitter, or a merger </dd>

  <dt> Submodule </dt>
  <dd> Functionality that one bioinformatics tools is providing. For example, <i>index</i> is Submodule for <i>samtools</i> Module </dd>

  <dt> Splitter </dt>
  <dd> A <b>Module</b> that splits an input file into multiple output files. </dd>

  <dt> Merger </dt>
  <dd> A Module that merges multiple input files of the same type into one single output file. </dd>

  <dt> Resource Kit </dt>
  <dd> List of bioinformatics tools or input resources (e.g. reference genome) necessary for a Pipeline</dd>

  <dt> Sample Sheet </dt>
  <dd> Input files that are processed by a Pipeline</dd>

  <dt> Platform </dt>
  <dd> A cloud computing service that runs a Pipeline. </dd>

  <dt> Processor </dt>
  <dd> An instance/server on a cloud computing platform. </dd>

  <dt> Task </dt>
  <dd> A command or set of instructions that a processor has to execute. </dd>

  <dt> Worker </dt>
  <dd> A processor that executes a task. </dd>

  <dt> Final Report </dt>
  <dd> A file containing the entire run metadata and statistics </dd>

  <dt> Report topic </dt>
  <dd> A messenging service that receives the final report of a run </dd>

</dl>