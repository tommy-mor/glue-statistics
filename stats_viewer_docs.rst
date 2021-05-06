
Working with Data objects
If you are using the IPython terminal in the Glue application, or if you are writing Python code that uses Glue, you will probably want to interact with data.

Data classes
The core data container in Glue is the :class:`~glue.core.data.Data` class. Each :class:`~glue.core.data.Data` instance can include any number of n-dimensional components, each represented by the :class:`~glue.core.component.Component` class. The actual data resides in the :class:`~glue.core.component.Component` objects. Because of this structure, a :class:`~glue.core.data.Data` object can represent either a table, which is a collection of 1-d :class:`~glue.core.component.Component` objects, or an n-dimensional dataset, which might include one (but could include more) n-dimensional :class:`~glue.core.component.Component` objects.

Inside :class:`~glue.core.data.Data` objects, each :class:`~glue.core.component.Component` is assigned a :class:`~glue.core.component_id.ComponentID`. However, this is not necessarily a unique ID for each and every component -- instead, different components representing the same conceptual quantity can be given the same component ID. Component IDs are central to the linking framework

When using the Glue application, the :class:`~glue.core.data.Data` objects are collected inside a :class:`~glue.core.data_collection.DataCollection`.

We can represent this graphically like this:
