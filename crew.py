from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import os


class MapCommand(BaseModel):
    """Map camera manipulation and styling command"""
    command: str = Field(..., description="Command type (flyTo, easeTo, jumpTo, fitBounds, setLights, setFog, setSnow, setRain)")
    params: Dict[str, Any] = Field(..., description="Parameters for the command")
    wait_for_completion: bool = Field(default=True, description="Whether to wait for animation to complete")


class GeoJSONGeometry(BaseModel):
    """GeoJSON Geometry model"""
    type: str = Field(..., description="Geometry type (Point, LineString, Polygon)")
    coordinates: List[Any] = Field(..., description="Coordinate array")


class GeoJSONProperties(BaseModel):
    """GeoJSON Feature properties"""
    name: Optional[str] = Field(None, description="Name of the geographic feature")
    description: Optional[str] = Field(None, description="Description of the geographic feature")


class GeoJSONFeature(BaseModel):
    """GeoJSON Feature model"""
    type: str = Field(default="Feature", description="Feature type")
    geometry: GeoJSONGeometry = Field(..., description="Feature geometry")
    properties: GeoJSONProperties = Field(..., description="Feature properties")


class GeoJSONFeatureCollection(BaseModel):
    """GeoJSON FeatureCollection model"""
    type: str = Field(default="FeatureCollection", description="FeatureCollection type")
    features: List[GeoJSONFeature] = Field(..., description="List of features")


class LocationResponse(BaseModel):
    """Structured response model containing text and GeoJSON data"""
    text: str = Field(..., description="Textual response to display to the user")
    geojson: Optional[GeoJSONFeatureCollection] = Field(
        None, 
        description="GeoJSON FeatureCollection representing geographic elements, null if no geographic data"
    )
    map_commands: Optional[List[MapCommand]] = Field(
        None,
        description="Optional list of map camera commands to choreograph map movements"
    )


@CrewBase
class DemoProject():
    """DemoProject crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    mcp_server_params = [
        {
            "url": "https://mcp.mapbox.com/mcp",
            "transport": "streamable-http",
            "headers": {"authorization": f"Bearer {os.environ['MAPBOX_ACCESS_TOKEN']}"}
        }
    ]

    @agent
    def helpful_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['helpful_agent'], # type: ignore[index]
            verbose=True,
            tools=self.get_mcp_tools()
        )
    @agent
    def geojson_enrichment_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['geojson_enrichment_agent'], # type: ignore[index]
            verbose=True
        )

    @agent
    def camera_choreographer_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['camera_choreographer_agent'], # type: ignore[index]
            verbose=True,
            tools=self.get_mcp_tools()
        )

    @task
    def help_task(self) -> Task:
        return Task(
            config=self.tasks_config['help_task'], # type: ignore[index]
        )
    @task
    def geojson_enrichment_task(self) -> Task:
        return Task(
            config=self.tasks_config['geojson_enrichment_task'], # type: ignore[index]
            output_json=LocationResponse
        )
        
    @task
    def camera_choreography_task(self) -> Task:
        return Task(
            config=self.tasks_config['camera_choreography_task'], # type: ignore[index]
            output_json=LocationResponse
        )

    @crew
    def crew(self) -> Crew:
        """Creates the DemoProject crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you want to use that instead https://docs.crewai.com/how-to/Hierarchical/
        )