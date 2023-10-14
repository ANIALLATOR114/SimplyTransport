from litestar import Controller, get, post
from litestar.di import Provide

from SimplyTransport.domain.example import (Example, ExampleModel,
                                            ExampleRepository,
                                            provide_example_repo)

__all__ = [
    "sampleController",
]


class SampleController(Controller):

    dependencies = {"example_repo": Provide(provide_example_repo)}

    @get("/")
    async def example(self, example_repo: ExampleRepository) -> list[Example]:
        result = await example_repo.list()
        return [Example.model_validate(obj) for obj in result]
    
    
    @post("/")
    async def example_create(self, example_repo: ExampleRepository) -> Example:
        obj = await example_repo.add(ExampleModel(name="default-name"))
        await example_repo.session.commit()
        return Example.model_validate(obj)
    

