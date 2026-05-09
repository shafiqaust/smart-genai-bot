class Node:
    def __init__(self, id: str, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description
        self.point_to: list["Node"] = []    # prerequisites: this node requires these
        self.point_from: list["Node"] = []  # dependents: these nodes require this one

    def add_point_to(self, target: "Node"):
        """Self → target: know self to understand target."""
        if target not in self.point_to:
            self.point_to.append(target)
        if self not in target.point_from:
            target.point_from.append(self)

    def add_point_from(self, source: "Node"):
        """Source → self: know source to understand self."""
        if source not in self.point_from:
            self.point_from.append(source)
        if self not in source.point_to:
            source.point_to.append(self)

    def __repr__(self):
        return f"Node({self.id!r})"

matrix_manipulation = Node(
    id="matrix_manipulation",
    name="Matrix Manipulation",
    description="An operation that takes two matrices and produces a third. Rows of the first matrix are combined with columns of the second via dot products.",
)

loss_function = Node(
    id="loss_function",
    name="Loss Function",
    description="A function that measures how far a model's output is from the desired output. Returns a single number — lower means better.",
)

gradient_descent = Node(
    id="gradient_descent",
    name="Gradient Descent",
    description="An optimisation algorithm that iteratively adjusts parameters to minimise a function by moving in the direction of the steepest decrease.",
)

neural_net = Node(
    id="neural_net",
    name="Neural Network",
    description="A computational model composed of layers of interconnected nodes. Maps an input to an output by passing data through successive transformations, and learns those transformations from examples.",
)

generator = Node(
    id="generator",
    name="Generator",
    description="A model that takes a random input and produces a synthetic output. Learns to generate outputs that are indistinguishable from real examples.",
)

discriminator = Node(
    id="discriminator",
    name="Discriminator",
    description="A model that takes an input and outputs a judgment of whether it is real or synthetic. Learns to distinguish genuine examples from generated ones.",
)

adversarial_training = Node(
    id="adversarial_training",
    name="Adversarial Training",
    description="A training procedure in which two models are pitted against each other. One tries to fool the other; the other tries not to be fooled. Each is updated independently using its own loss signal.",
)

GAN = Node(
    id="GAN",
    name="Generative Adversarial Network",
    description="A framework in which two models are trained simultaneously in opposition. One model generates synthetic outputs; the other evaluates their authenticity. Their competition drives both to improve.",
)


random_noise = Node(
    id="random_noise",
    name="Random Noise",
    description="A vector of values sampled randomly from a distribution. Used as a starting point for generation — different samples produce different outputs.",
)

image = Node(
    id="image",
    name="Image",
    description="A structured grid of values representing visual data. Used as both the target output of generation and the input to evaluation.",
)

separate_losses = Node(
    id="separate_losses",
    name="Separate Losses",
    description="A training setup where two competing models each have their own independent loss function and are updated separately rather than jointly.",
)

training_balance = Node(
    id="training_balance",
    name="Training Balance",
    description="The condition in which two competing models improve at a similar rate. If one becomes too strong, the other stops receiving a useful learning signal.",
)

mode_collapse = Node(
    id="mode_collapse",
    name="Mode Collapse",
    description="A failure mode in which a generative model produces only a narrow range of outputs, ignoring the full diversity of the target distribution.",
)


# ── edges (A → B means: know A to understand B) ──────────────────────────────
loss_function.add_point_to(gradient_descent)
loss_function.add_point_to(neural_net)
matrix_manipulation.add_point_to(neural_net)
gradient_descent.add_point_to(neural_net)
neural_net.add_point_to(generator)
neural_net.add_point_to(discriminator)
random_noise.add_point_to(generator)
image.add_point_to(generator)
image.add_point_to(discriminator)
generator.add_point_to(adversarial_training)
discriminator.add_point_to(adversarial_training)
loss_function.add_point_to(adversarial_training)
adversarial_training.add_point_to(separate_losses)
generator.add_point_to(GAN)
discriminator.add_point_to(GAN)
adversarial_training.add_point_to(GAN)
separate_losses.add_point_to(training_balance)
GAN.add_point_to(mode_collapse)
training_balance.add_point_to(mode_collapse)
