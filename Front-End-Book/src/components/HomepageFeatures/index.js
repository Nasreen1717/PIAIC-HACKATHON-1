import Link from '@docusaurus/Link';
import styles from './styles.module.css';

const ModuleList = [
  {
    icon: '🤖',
    title: 'Module 1: ROS 2',
    description: 'Master robotic middleware & control systems. Learn nodes, topics, and services.',
    link: '/docs/module-1/intro',
    comingSoon: false,
  },
  {
    icon: '🌐',
    title: 'Module 2: Simulation',
    description: 'Digital twins & physics engines. Gazebo, URDF, and realistic simulation.',
    link: '/docs/module-2/intro',
    comingSoon: false,
  },
  {
    icon: '👁️',
    title: 'Module 3: Isaac AI',
    description: 'Advanced perception & training. AI-powered robotics and computer vision.',
    link: '/docs/module-3/intro',
    comingSoon: false,
  },
  {
    icon: '🔄',
    title: 'Module 4: VLA',
    description: 'Vision-Language-Action. LLMs meet robotics for autonomous reasoning.',
    link: '/docs/module-4/intro',
    comingSoon: false,
  },
  {
    icon: '🚀',
    title: 'Module 5: Advanced Topics',
    description: 'Deep dive into cutting-edge robotics research and emerging technologies.',
    link: '#',
    comingSoon: true,
  },
  {
    icon: '🏭',
    title: 'Module 6: Real-World Applications',
    description: 'Deploy AI-powered robotics solutions in production environments.',
    link: '#',
    comingSoon: true,
  },
];

function ModuleCard({ icon, title, description, link, index, comingSoon }) {
  const cardContent = (
    <div className={`${styles.moduleCard} ${comingSoon ? styles.moduleCardComingSoon : ''}`} style={{
      animation: `fadeInUp 0.6s ease-out ${0.1 + (index * 0.1)}s both`,
      opacity: comingSoon ? 0.85 : 1,
      pointerEvents: comingSoon ? 'none' : 'auto',
    }}>
      <div className={styles.moduleIcon}>{icon}</div>
      <h3 className={styles.moduleTitle}>{title}</h3>
      <p className={styles.moduleDescription}>{description}</p>
      {comingSoon ? (
        <div className={styles.moduleComingSoon}>Coming Soon ✨</div>
      ) : (
        <div className={styles.moduleLink}>Learn more →</div>
      )}
    </div>
  );

  if (comingSoon) {
    return cardContent;
  }

  return (
    <Link to={link} className={styles.moduleCardLink}>
      {cardContent}
    </Link>
  );
}

export default function HomepageFeatures() {
  return (
    <section id="modules" className={styles.modulesSection}>
      <div className={styles.modulesContainer}>
        <div className={styles.modulesHeader}>
          <h2 style={{fontSize: '2.5rem', marginBottom: '1rem', color: '#334155'}}>
            📚 Learning Modules
          </h2>
          <p style={{fontSize: '1.1rem', opacity: 0.8, maxWidth: '500px', margin: '0 auto', color: '#475569'}}>
            Master Physical AI & Humanoid Robotics through our comprehensive, hands-on modules
          </p>
        </div>
        <div className={styles.modulesGrid}>
          {ModuleList.map((module, idx) => (
            <ModuleCard key={idx} index={idx} {...module} />
          ))}
        </div>
      </div>
    </section>
  );
}
